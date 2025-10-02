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
  GetFieldLevelEncryptionRequest,
  GetFieldLevelEncryptionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetFieldLevelEncryptionCommandInput
  extends GetFieldLevelEncryptionRequest {}
export interface GetFieldLevelEncryptionCommandOutput
  extends GetFieldLevelEncryptionResult,
    __MetadataBearer {}
export declare class GetFieldLevelEncryptionCommand extends $Command<
  GetFieldLevelEncryptionCommandInput,
  GetFieldLevelEncryptionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetFieldLevelEncryptionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetFieldLevelEncryptionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetFieldLevelEncryptionCommandInput,
    GetFieldLevelEncryptionCommandOutput
  >;
  private serialize;
  private deserialize;
}
