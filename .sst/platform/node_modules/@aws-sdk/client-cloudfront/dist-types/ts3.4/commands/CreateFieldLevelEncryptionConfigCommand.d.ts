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
  CreateFieldLevelEncryptionConfigRequest,
  CreateFieldLevelEncryptionConfigResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateFieldLevelEncryptionConfigCommandInput
  extends CreateFieldLevelEncryptionConfigRequest {}
export interface CreateFieldLevelEncryptionConfigCommandOutput
  extends CreateFieldLevelEncryptionConfigResult,
    __MetadataBearer {}
export declare class CreateFieldLevelEncryptionConfigCommand extends $Command<
  CreateFieldLevelEncryptionConfigCommandInput,
  CreateFieldLevelEncryptionConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateFieldLevelEncryptionConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateFieldLevelEncryptionConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateFieldLevelEncryptionConfigCommandInput,
    CreateFieldLevelEncryptionConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
