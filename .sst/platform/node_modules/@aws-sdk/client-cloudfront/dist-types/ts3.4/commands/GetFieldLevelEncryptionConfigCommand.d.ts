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
  GetFieldLevelEncryptionConfigRequest,
  GetFieldLevelEncryptionConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetFieldLevelEncryptionConfigCommandInput
  extends GetFieldLevelEncryptionConfigRequest {}
export interface GetFieldLevelEncryptionConfigCommandOutput
  extends GetFieldLevelEncryptionConfigResult,
    __MetadataBearer {}
export declare class GetFieldLevelEncryptionConfigCommand extends $Command<
  GetFieldLevelEncryptionConfigCommandInput,
  GetFieldLevelEncryptionConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetFieldLevelEncryptionConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetFieldLevelEncryptionConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetFieldLevelEncryptionConfigCommandInput,
    GetFieldLevelEncryptionConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
