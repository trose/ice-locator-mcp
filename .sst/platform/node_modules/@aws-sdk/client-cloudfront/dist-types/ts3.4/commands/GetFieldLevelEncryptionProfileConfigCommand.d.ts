import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  GetFieldLevelEncryptionProfileConfigRequest,
  GetFieldLevelEncryptionProfileConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetFieldLevelEncryptionProfileConfigCommandInput
  extends GetFieldLevelEncryptionProfileConfigRequest {}
export interface GetFieldLevelEncryptionProfileConfigCommandOutput
  extends GetFieldLevelEncryptionProfileConfigResult,
    __MetadataBearer {}
export declare class GetFieldLevelEncryptionProfileConfigCommand extends $Command<
  GetFieldLevelEncryptionProfileConfigCommandInput,
  GetFieldLevelEncryptionProfileConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetFieldLevelEncryptionProfileConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetFieldLevelEncryptionProfileConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetFieldLevelEncryptionProfileConfigCommandInput,
    GetFieldLevelEncryptionProfileConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
